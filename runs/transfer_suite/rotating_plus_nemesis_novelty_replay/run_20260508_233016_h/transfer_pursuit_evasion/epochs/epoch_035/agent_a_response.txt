def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in self_role) or ("tag" in self_role) or ("hunter" in self_role) or (("purs" in opp_role) or ("tag" in opp_role) or ("hunter" in opp_role))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs_dist(start):
        if start == (ox, oy):
            return 0
        qx, qy, qi = [start[0]], [start[1]], 0
        dist = {(start[0], start[1]): 0}
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[(x, y)] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked and (nx, ny) not in dist:
                    if nx == ox and ny == oy:
                        return nd
                    dist[(nx, ny)] = nd
                    qx.append(nx); qy.append(ny)
        return None

    best_move, best_val = (0, 0), None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        d = bfs_dist((nx, ny))
        if d is None:
            # No path: prefer staying out of dead-ends if possible (heuristic)
            d = (abs(nx - ox) + abs(ny - oy)) * 2 + 1000
        # pursuer: minimize path distance; evader: maximize
        val = -d if pursuer else d
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]