def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = observation.get("self_role", "pursuer")
    if role not in ("pursuer", "evader"):
        role = "pursuer"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if role == "evader":
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), c[0] + c[1]))
        best = (-(10**9), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                sc = abs(nx - ox) + abs(ny - oy) + (abs(nx - tx) + abs(ny - ty)) * 0.01
                if sc > best[0]:
                    best = (sc, dx, dy)
        return [int(best[1]), int(best[2])]

    # pursuer: greedy step along BFS shortest distance to opponent, with wall-run resilience via farthest-reachable tie-break
    dist = [[None] * h for _ in range(w)]
    if 0 <= ox < w and 0 <= oy < h and (ox, oy) not in obs:
        q = [(ox, oy)]
        dist[ox][oy] = 0
        qi = 0
        while qi < len(q):
            cx, cy = q[qi]
            qi += 1
            nd = dist[cx][cy] + 1
            for dx, dy in moves:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and dist[nx][ny] is None:
                    dist[nx][ny] = nd
                    q.append((nx, ny))

    def reachable_score(x, y):
        # small deterministic flood count from candidate to prefer safer corridors
        seen = set([(x, y)])
        frontier = [(x, y)]
        steps = 0
        while frontier and steps < 20:
            cx, cy = frontier.pop()
            steps += 1
            for dx, dy in moves:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    frontier.append((nx, ny))
        return len(seen)

    best = (10**18, -10**9, 0, 0)  # (dist, -safety, tie, move)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            d = dist[nx][ny]
            if d is None:
                # fallback: minimize manhattan distance if opponent dist unreachable
                d2 = abs(nx - ox) + abs(ny - oy)
                safety = reachable_score(nx, ny)
                key = (d2, -safety, 0)
            else:
                safety = reachable_score(nx, ny)
                key = (d, -safety, abs(nx - ox) + abs(ny - oy))
            if key[0] < best[0] or (key[0] == best[0] and key[1] < best[1]):
                best = (key[0], key[1], key[2], dx, dy)

    return [int(best[3]), int(best[4])]