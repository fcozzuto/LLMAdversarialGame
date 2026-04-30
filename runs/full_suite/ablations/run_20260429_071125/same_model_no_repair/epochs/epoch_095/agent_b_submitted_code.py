def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs(start):
        dist = {start: 0}
        q = [start]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[(x, y)] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    if (nx, ny) not in dist:
                        dist[(nx, ny)] = nd
                        q.append((nx, ny))
        return dist

    my_dist = bfs((sx, sy))
    op_dist = bfs((ox, oy))

    def best_step(target):
        tx, ty = target
        best = (10**9, 0, 0)
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = my_dist.get((nx, ny), 10**9)
                # Prefer decreasing distance-to-target by BFS distance
                tmy = my_dist.get((tx, ty), 10**9)
                score = (0 if d < tmy else 1, d, abs(nx - tx) + abs(ny - ty))
                if score < best[0:3]:
                    best = (score, dx, dy)
        return [best[1], best[2]]

    candidates = []
    for rx, ry in resources:
        md = my_dist.get((rx, ry), 10**9)
        od = op_dist.get((rx, ry), 10**9)
        if md >= 10**9 and od >= 10**9:
            continue
        candidates.append((rx, ry, md, od))

    # Prefer races we can win; otherwise maximize opponent disadvantage.
    feasible_win = [c for c in candidates if c[2] <= c[3] and c[2] < 10**9]
    pool = feasible_win if feasible_win else candidates
    if not pool:
        return [0, 0]

    # Tie-break deterministically by coords
    rx, ry, md, od = min(
        pool,
        key=lambda c: (
            -1 if c in feasible_win else 0,
            -(c[3] - c[2] if c[2] < 10**9 and c[3] < 10**9 else -10**9),
            c[2],
            c[0],
            c[1],
        ),
    )
    # Small denial: if opponent can reach much sooner to this resource, consider a neighbor cell of it.