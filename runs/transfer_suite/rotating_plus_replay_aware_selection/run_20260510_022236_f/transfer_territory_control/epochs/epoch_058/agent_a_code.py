def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs_best(start, targets, maxd=8):
        if start in obstacles:
            return None
        if not targets:
            return None
        q = [(start[0], start[1], 0)]
        seen = {start}
        best = None
        qi = 0
        while qi < len(q):
            x, y, d = q[qi]
            qi += 1
            if (x, y) in targets:
                best = d
                break
            if d >= maxd:
                continue
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append((nx, ny, d + 1))
        return best

    targets1 = {c for c in unclaimed if inb(c[0], c[1]) and c not in obstacles}
    targets2 = {c for c in op_terr if inb(c[0], c[1]) and c not in obstacles}

    cur = (sx, sy)
    best_score = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        p = (nx, ny)
        d1 = bfs_best(p, targets1)
        d2 = bfs_best(p, targets2)
        score = 10**9
        if d1 is not None:
            score = d1
        elif d2 is not None:
            score = 1000 + d2
        else:
            score = 2000 + abs(nx - ox) + abs(ny - oy)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]