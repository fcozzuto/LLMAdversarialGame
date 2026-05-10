def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda m: (m[0], m[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or (self_role in ("captor", "pursuer"))
    evader = not pursuer

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    # Deterministic local "path pressure": 2-step lookahead with obstacle avoidance
    def best_for(target_x, target_y, mode):
        best_score = None
        best = (0, 0)
        for dx1, dy1 in moves:
            x1, y1 = sx + dx1, sy + dy1
            if not inb(x1, y1):
                continue
            # Hard avoid stepping onto immediate opponent position when pursuing
            if pursuer and x1 == ox and y1 == oy:
                score = 10**9
            else:
                score = -dist2(x1, y1, target_x, target_y) if mode == "pursue" else dist2(x1, y1, target_x, target_y)
                # second step: choose neighbor that best continues the objective
                best2 = None
                for dx2, dy2 in moves:
                    x2, y2 = x1 + dx2, y1 + dy2
                    if not inb(x2, y2):
                        continue
                    val = -dist2(x2, y2, target_x, target_y) if mode == "pursue" else dist2(x2, y2, target_x, target_y)
                    if best2 is None or ((mode == "pursue" and val > best2) or (mode != "pursue" and val > best2)):
                        best2 = val
                if best2 is not None:
                    score += 0.35 * best2
                # small tie-breaker: prefer moves that keep mobility
                mobility = 0
                for dxm, dym in moves:
                    xm, ym = x1 + dxm, y1 + dym
                    if inb(xm, ym):
                        mobility += 1
                score += (0.01 * mobility)
                # small bias to continue direction (reduces zigzag suicide)
                score += 0.002 * (dx1 * dx1 + dy1 * dy1)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx1, dy1)
        return list(best)

    if pursuer:
        # target is opponent position; if blocked, slight bias toward the "farthest frontier" that still reduces distance
        tx, ty = ox, oy
        return best_for(tx, ty, "pursue")
    else:
        # Evade: maximize distance to opponent, but also avoid reducing distance too much next move
        return best_for(ox, oy, "evade")