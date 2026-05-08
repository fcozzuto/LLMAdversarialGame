def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors(pos):
        px, py = pos
        res = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if ok(nx, ny):
                res.append((nx, ny))
        if not res:
            res = [(px, py)]
        return res

    my_pos = (sx, sy)
    opp_pos = (ox, oy)
    my_moves = neighbors(my_pos)
    opp_moves = neighbors(opp_pos)

    best = None
    best_val = None

    # Deterministic tie-breaker: fixed move order by deltas
    move_to_delta = {my_pos2: (my_pos2[0] - sx, my_pos2[1] - sy) for my_pos2 in my_moves}

    for my2 in my_moves:
        md = move_to_delta[my2]
        # After we move, assume opponent chooses their best for their role
        if self_is_evader:
            # Evader wants to maximize opponent distance, so opponent (pursuer) minimizes our distance
            worst = None
            for op2 in opp_moves:
                d = dist(my2, op2)
                val = d
                if worst is None or val < worst:
                    worst = val
            # Prefer larger distance; also keep mobility
            mob = len(neighbors(my2))
            val = (worst, mob, -abs(md[0]) - abs(md[1]))
            if best_val is None or val > best_val:
                best_val, best = val, md
        else:
            # Pursuer wants to minimize distance after both move
            best_for_me = None
            for op2 in opp_moves:
                d = dist(my2, op2)
                val = -d
                if best_for_me is None or val > best_for_me:
                    best_for_me = val
            # If capture possible (distance 0), prioritize strongly
            cap = 1 if (my2 == opp_pos) else 0
            mob = len(neighbors(my2))
            val = (cap, best_for_me, mob, -abs(md[0]) - abs(md[1]))
            if best_val is None or val > best_val:
                best_val, best = val, md

    dx, dy = best if best is not None else (0, 0)
    dx = int(dx)
    dy = int(dy)
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]