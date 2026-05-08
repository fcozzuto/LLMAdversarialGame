def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = any(k in role_s for k in ("evader", "runner", "flee", "avoid", "escape"))
    is_pursuer = any(k in role_s for k in ("pursuer", "chaser", "hunter", "catch", "pursuit"))
    pursuer = is_pursuer or (not is_evader)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def sqdist(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_pen(x, y):
        # Penalize being adjacent to obstacles so evader doesn't get trapped by runners on walls.
        pen = 0
        for nx in (x - 1, x, x + 1):
            for ny in (y - 1, y, y + 1):
                if (nx, ny) in blocked:
                    pen += 1
        return pen

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        d0 = sqdist(nx, ny, ox, oy)

        # One-step lookahead against a simple opponent response:
        # If we are pursuer, assume opponent moves to increase distance; if evader, assume opponent moves to decrease.
        # Deterministic: we choose the worst/best response among all legal opponent moves.
        opp_best = None
        for odx, ody in deltas:
            tx, ty = ox + odx, oy + ody
            if tx < 0 or tx >= w or ty < 0 or ty >= h:
                continue
            if (tx, ty) in blocked:
                continue
            td = sqdist(nx, ny, tx, ty)
            if pursuer:
                # opponent tries to maximize distance from us
                val = td
                if opp_best is None or val > opp_best:
                    opp_best = val
            else:
                # opponent tries to minimize distance to us
                val = td
                if opp_best is None or val < opp_best:
                    opp_best = val

        # Immediate capture check (radius 0): moving onto opponent cell wins for pursuer, loses for evader.
        if nx == ox and ny == oy:
            val = 10_000_000 if pursuer else -10_000_000
        else:
            # Additional tie-break prefers moving toward/away from opponent with obstacle awareness.
            pen = obstacle_pen(nx, ny)
            if pursuer:
                # minimize distance; penalize adjacency a bit to avoid dead ends
                val = -(d0 * 10) + (opp_best is not None and -(opp_best * 1)) - (pen * 3)
            else:
                # maximize distance; strongly avoid obstacles to prevent getting cornered
                val = (d0 * 10) - (opp_best is not None and (opp_best * 1)) - (pen * 6)

        if best_val is None or (val > best_val):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]