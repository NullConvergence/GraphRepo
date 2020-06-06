from datetime import datetime


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def index_commits(graph, commits, batch_size=100):
    query = """
    UNWIND {commits} AS c
    MERGE (:Commit { hash: c.hash,
                     timestamp: c.timestamp,
                     is_merge: c.is_merge,
                     project_id: c.project_id})
    """
    for b in batch(commits, batch_size):
        graph.run(query, commits=b)


def index_parent_commits(graph, parents, batch_size=100):
    query = """
    UNWIND {ac} AS a
    MATCH (x:Commit),(y:Commit)
    WHERE x.hash = a.parent_hash AND y.hash = a.child_hash
    MERGE (x)-[r:Parent{}]->(y)
    """
    for b in batch(parents, batch_size):
        graph.run(query, ac=b)


def index_authors(graph, authors, batch_size=100):
    query = """
    UNWIND {authors} AS a
    MERGE (:Developer { hash: a.hash,
                        email: a.email,
                        name: a.name
                      })
    """
    if batch_size:
        for b in batch(authors, batch_size):
            graph.run(query, authors=b)
    else:
        graph.run(query, authors=authors)


def index_branches(graph, branches, batch_size=100):
    query = """
    UNWIND {branches} AS a
    MERGE (:Branch { hash: a.hash,
                     name:a.name,
                     project_id: a.project_id})
    """
    for b in batch(branches, batch_size):
        graph.run(query, branches=b)


def index_branch_commits(graph, bc, batch_size=100):
    query = """
    UNWIND {ac} AS a
    MATCH (x:Branch),(y:Commit)
    WHERE x.hash = a.branch_hash AND y.hash = a.commit_hash
    MERGE (x)-[r:BranchCommit{}]->(y)
    """
    for b in batch(bc, batch_size):
        graph.run(query, ac=b)


def index_files(graph, files, batch_size=100):
    query = """
    UNWIND {files} AS f
    MERGE (:File { hash: f.hash,
                   project_id: f.project_id,
                   type:f.type, name: f.name})
    """
    if batch_size:
        for b in batch(files, batch_size):
            graph.run(query, files=b)
    else:
        graph.run(query, files=files)


def index_methods(graph, methods, batch_size=100):
    query = """
    UNWIND {methods} AS f
    MERGE (:Method { hash: f.hash,
                     project_id: f.project_id,
                     name: f.name,
                     file_name: f.file_name})
    """
    if batch_size:
        for b in batch(methods, batch_size):
            graph.run(query, methods=b)
    else:
        graph.run(query, methods=methods)


def index_author_commits(graph, ac, batch_size=100):
    query = """
    UNWIND {ac} AS a
    MATCH (x:Developer),(y:Commit)
    WHERE x.hash = a.author_hash AND y.hash = a.commit_hash
    MERGE (x)-[r:Author{timestamp: a.timestamp}]->(y)
    """
    for b in batch(ac, batch_size):
        graph.run(query, ac=b)


def index_commit_files(graph, cf, batch_size=100):
    query = """
    UNWIND {cf} AS a
    MATCH (x:Commit),(y:File)
    WHERE x.hash = a.commit_hash AND y.hash = a.file_hash
    MERGE (x)-[r:UpdateFile{}]->(y)
    ON CREATE SET r=a['attributes']
    """
    for i, b in enumerate(batch(cf, batch_size)):
        graph.run(query, cf=b)


def index_file_methods(graph, cf, batch_size=100):
    query = """
    UNWIND {cf} AS a
    MATCH (x:File),(y:Method)
    WHERE x.hash = a.file_hash AND y.hash = a.method_hash
    MERGE (x)-[r:Method{}]->(y)
    """
    for b in batch(cf, batch_size):
        graph.run(query, cf=b)


def index_commit_method(graph, cm, batch_size=100):
    query = """
    UNWIND {cf} AS a
    MATCH (x:Commit),(y:Method)
    WHERE x.hash = a.commit_hash AND y.hash = a.method_hash
    MERGE (x)-[r:UpdateMethod]->(y)
    ON CREATE SET r=a['attributes']
    """
    for i, b in enumerate(batch(cm, batch_size)):
        graph.run(query, cf=b)


def create_index_authors(graph):
    query = """
    CREATE INDEX ON :Developer(hash)
    """
    graph.run(query)


def create_index_commits(graph):
    hash_q = """
    CREATE INDEX ON :Commit(hash)
    """
    pid_q = """
    CREATE INDEX ON :Commit(project_id)
    """
    graph.run(hash_q)
    graph.run(pid_q)


def create_index_branches(graph):
    hash_q = """
    CREATE INDEX ON :Branch(hash)
    """
    pid_q = """
    CREATE INDEX ON :Branch(project_id)
    """
    graph.run(hash_q)
    graph.run(pid_q)


def create_index_files(graph):
    hash_q = """
    CREATE INDEX ON :File(hash)
    """
    pid_q = """
    CREATE INDEX ON :File(project_id)
    """
    graph.run(hash_q)
    graph.run(pid_q)


def create_index_methods(graph):
    hash_q = """
    CREATE INDEX ON :Method(hash)
    """
    pid_q = """
    CREATE INDEX ON :Method(project_id)
    """
    graph.run(hash_q)
    graph.run(pid_q)


def index_all(graph, developers, commits, parents, dev_commits, branches,
              branches_commits, files, commit_files, methods, file_methods,
              commit_methods, batch_size=100):
    parents = list({str(i): i for i in parents}.values())
    developers = list({v['hash']: v for v in developers}.values())
    branches = list({v['hash']: v for v in branches}.values())
    branches_commits = list({str(i): i for i in branches_commits}.values())

    files = list({v['hash']: v for v in files}.values())
    methods = list({v['hash']: v for v in methods}.values())
    file_methods = list({str(i): i for i in file_methods}.values())
    total = datetime.now()

    print('Indexing ', len(developers), ' authors')
    start = datetime.now()
    index_authors(graph, developers, batch_size)
    create_index_authors(graph)
    print('Indexed authors in: \t', datetime.now()-start)

    print('Indexing ', len(commits), ' commits')
    start = datetime.now()
    index_commits(graph, commits, batch_size)
    create_index_commits(graph)
    print('Indexed commits in: \t', datetime.now()-start)

    print('Indexing ', len(branches), ' branches')
    start = datetime.now()
    index_branches(graph, branches, batch_size)
    create_index_branches(graph)
    index_branch_commits(graph, branches_commits, batch_size)
    print('Indexed branches in: \t', datetime.now()-start)

    print('Indexing ', len(files), ' files')
    start = datetime.now()
    index_files(graph, files, batch_size)
    create_index_files(graph)
    print('Indexed files in: \t', datetime.now()-start)

    print('Indexing ', len(methods), ' methods')
    start = datetime.now()
    index_methods(graph, methods, batch_size)
    create_index_methods(graph)
    print('Indexed methods in: \t', datetime.now()-start)

    print('Indexing ', len(parents), ' parent commits')
    start = datetime.now()
    index_parent_commits(graph, parents, batch_size)
    print('Indexed commits in: \t', datetime.now()-start)

    print('Indexing ', len(dev_commits), ' author_commits')
    start = datetime.now()
    index_author_commits(graph, dev_commits, batch_size)
    print('Indexed author_commits in: \t', datetime.now()-start)

    print('Indexings ', len(file_methods), ' file_methods')
    start = datetime.now()
    index_file_methods(graph, file_methods, batch_size)
    print('Indexed file_methods in: \t', datetime.now()-start)

    print('Indexing ', len(commit_methods), ' commit_methods')
    start = datetime.now()
    index_commit_method(graph, commit_methods, batch_size)
    print('Indexed commit_methods in: \t', datetime.now()-start)

    print('Indexing ', len(commit_files), ' commit_files')
    start = datetime.now()
    index_commit_files(graph, commit_files, batch_size)
    print('Indexed commit_files in: \t', datetime.now()-start)

    print('Indexing took: \t', datetime.now()-total)
