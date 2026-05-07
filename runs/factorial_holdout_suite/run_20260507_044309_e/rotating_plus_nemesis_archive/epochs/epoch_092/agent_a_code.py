def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in (observation.get("obstacles") or []):
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    prefer = int(observation.get("turn_index") or 0) % 4  # deterministic phase shift

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            # Two-mode: sometimes race opponent (closer resources), sometimes deny by choosing resources farther from opponent.
            if prefer in (0, 1):
                # race: minimize (d_self - 0.6*d_opp)
                val = None
                for rx, ry in resources:
                    d_self = cheb(nx, ny, rx, ry)
                    d_opp = cheb(ox, oy, rx, ry)
                    cand = d_self - 0.6 * d_opp
                    if val is None or cand < val or (cand == val and (rx, ry) < best_move):
                        val = cand
                score = val
            else:
                # deny: minimize (d_self + 0.9*d_opp) to prefer resources opponent is far from
                val = None
                for rx, ry in resources:
                    d_self = cheb(nx, ny, rx, ry)
                    d_opp = cheb(ox, oy, rx, ry)
                    cand = d_self + 0.9 * d_opp
                    if val is None or cand < val or (cand == val and (rx, ry) < best_move):
                        val = cand
                score = val

            # micro-tie: prefer moves that reduce self distance to nearest resource
            md = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            score2 = (score, md, nx, ny)
        else:
            # no resources: drift toward center-ish, also away from opponent slightly
            center_x, center_y = (w - 1) // 2, (h - 1) // 2
            d_center = cheb(nx, ny, center_x, center_y)
            d_opp = cheb(nx, ny, ox, oy)
            score2 = (d_center - 0.1 * d_opp, nx, ny)

        if best_val is None or score2 < best_val:
            best_val = score2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]