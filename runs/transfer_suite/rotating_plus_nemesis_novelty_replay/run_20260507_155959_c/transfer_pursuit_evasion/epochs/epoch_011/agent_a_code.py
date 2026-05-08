def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr) or ("pursuer" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(start, target):
        if not inb(start[0], start[1]) or not inb(target[0], target[1]):
            return 10**9
        if start == target:
            return 0
        q = [start]
        qi = 0
        dist = {start: 0}
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[(x, y)] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in dist:
                    if (nx, ny) == target:
                        return nd
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return 10**9

    # Guess evader's escape corner: farthest from our current position.
    esc = max(corners, key=lambda c: bfs_dist((ox, oy), c) if inb(c[0], c[1]) else -1)

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_opp = bfs_dist((nx, ny), (ox, oy))
        d_esc = bfs_dist((nx, ny), esc)

        # Ensure determinism with a small grid-tie breaker.
        tie = (nx * 31 + ny) * 1e-6

        if pursuer:
            score = -d_opp - 0.06 * d_esc - tie
        else:
            score = d_opp + 0.06 * d_esc - tie

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]