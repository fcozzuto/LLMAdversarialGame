def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def bfs_first_step(start, goal):
        if start == goal:
            return (0, 0)
        q = [start]
        prev = {start: None}
        while q:
            x, y = q.pop(0)
            if (x, y) == goal:
                break
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or (nx, ny) in obs_set:
                    continue
                if (nx, ny) in prev:
                    continue
                prev[(nx, ny)] = (x, y)
                q.append((nx, ny))
        if goal not in prev:
            return None
        cur = goal
        while prev[cur] != start:
            cur = prev[cur]
        px, py = prev[cur]
        return (cur[0] - px, cur[1] - py)

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_key = None
    for rx, ry in resources:
        # Prefer reachable targets and those we can reach earlier than opponent.
        d_self = manhattan((sx, sy), (rx, ry))
        d_opp = manhattan((ox, oy), (rx, ry))
        # Strong bias to smaller self distance; slight bias for being earlier than opponent.
        key = (d_self - 0.35 * d_opp, d_self, -d_opp, rx, ry)
        if best_key is None or key < best_key:
            step = bfs_first_step((sx, sy), (rx, ry))
            if step is None:
                continue
            best_key = key
            best = step

    if best is not None:
        return [int(best[0]), int(best[1])]

    # Fallback: simple greedy to the nearest resource using straight-line step.
    tx, ty = min(resources, key=lambda r: manhattan((sx, sy), r))
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + dx, sy + dy
    if not inb(nx, ny) or (nx, ny) in obs_set:
        # Try axis-aligned alternative, then stay.
        for ndx, ndy in [(dx, 0), (0, dy), (-dx, 0), (0, -dy), (0, 0)]:
            nx2, ny2 = sx + ndx, sy + ndy
            if inb(nx2, ny2) and (nx2, ny2) not in obs_set:
                return [int(ndx), int(ndy)]
        return [0, 0]
    return [int(dx), int(dy)]