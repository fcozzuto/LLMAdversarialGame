def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    is_pursuer = any(k in sr for k in ("pursuer", "hunter", "chaser"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(start):
        if not inb(start[0], start[1]):
            return {}
        dist = {start: 0}
        q = [start]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[(x, y)] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in dist:
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return dist

    dist_from_self = bfs_dist((sx, sy))
    dist_to_opp = bfs_dist((ox, oy))  # dist_to_opp[p] = shortest turns from opp to p

    def manhattan(x, y):
        return abs(x - ox) + abs(y - oy)

    best = (None, None, None)  # (score, nx, ny)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if dist_to_opp:
            d = dist_to_opp.get((nx, ny), None)
        else:
            d = None

        if d is None:
            # unreachable: fallback on Manhattan
            d = manhattan(nx, ny)

        # Pursuer: minimize distance to opponent; Evader: maximize distance to opponent.
        score = -d if not is_pursuer else d

        # Deterministic tie-break: prefer moves that reduce/extend Manhattan, then lexicographic.
        if best[0] is None:
            best = (score, nx, ny)
            continue
        if score < best[0] if is_pursuer else score > best[0]:
            best = (score, nx, ny)
        elif score == best[0]:
            cur_m = manhattan(nx, ny)
            best_m = manhattan(best[1], best[2])
            if (cur_m < best_m and is_pursuer) or (cur_m > best_m and not is_pursuer):
                best = (score, nx, ny)
            elif cur_m == best_m:
                if (nx, ny) < (best[1], best[2]):
                    best = (score, nx, ny)

    if best[1] is None:
        return [0, 0]
    return [best[1] - sx, best[2] - sy]