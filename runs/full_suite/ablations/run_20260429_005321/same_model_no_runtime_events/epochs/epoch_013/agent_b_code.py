def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            t = (int(p[0]), int(p[1]))
            if t not in obstacles:
                resources.append(t)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            # Target the resource where we gain the most lead over the opponent.
            # Lead = opp_dist - my_dist (bigger is better).
            val = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Extra push for immediate reach.
                immed = 3 if myd == 0 else (2 if myd == 1 else 0)
                # Slight tie-break toward being central-ish to reduce stalls.
                center = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
                cand = (opd - myd) * 10 + immed * 7 - center
                if cand > val:
                    val = cand
            # Small preference for staying consistent: don't blow up distance to best target too much.
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # No resources visible: head toward center then toward opponent-corner diagonal pressure.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            to_center = cheb(nx, ny, cx, cy)
            to_opp = cheb(nx, ny, ox, oy)
            # Prefer closer to center; if equal, prefer moving away from opponent to avoid chase.
            val = -to_center * 10 - (-to_opp)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]