def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr) or ("pursuer" in sr)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(a, b):
        if not inb(a[0], a[1]) or not inb(b[0], b[1]):
            return 10**9
        if a == b:
            return 0
        q = [a]
        qi = 0
        dist = {a: 0}
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[(x, y)] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in dist:
                    if (nx, ny) == b:
                        return nd
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return 10**9

    def best_opp_move(my_next, opp_pos):
        # If we are pursuer, opponent (evader) maximizes distance; else minimizes distance.
        cur = opp_pos
        best = None
        best_val = None
        for dx, dy in deltas:
            nx, ny = cur[0] + dx, cur[1] + dy
            if not inb(nx, ny):
                nx, ny = cur
            d = bfs_dist((nx, ny), my_next)
            val = d if pursuer else -d
            if best is None or val > best_val or (val == best_val and (nx, ny) < best):
                best = (nx, ny)
                best_val = val
        return best

    best_self = (sx, sy)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        opp_next = best_opp_move((nx, ny), (ox, oy))
        d_after = bfs_dist(opp_next, (nx, ny))
        # Pursuer: minimize distance; Evader: maximize distance; tie-break closer to "safe" corner for evader / closer for pursuer.
        corner = (0 if pursuer else (w - 1)) , (0 if pursuer else (h - 1))
        safety = abs((w - 1) - opp_next[0]) + abs((h - 1) - opp_next[1])
        score = -d_after if pursuer else d_after
        score += (-0.01 * safety) if pursuer else (0.01 * safety)
        if best_score is None or score > best_score or (score == best_score and (nx, ny) < best_self):
            best_score = score
            best_self = (nx, ny)

    return [best_self[0] - sx, best_self[1] - sy]