def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    me_evader = ("evad" in self_role) or ("escape" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def opp_obj(dist, opp_is_evader):
        return dist if opp_is_evader else -dist

    opp_evader = not me_evader

    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d0 = cheb(nx, ny, ox, oy)

        # Opponent response (1 step): choose their best move toward their objective
        best_opp = None
        best_opp_val = None
        for odx, ody in moves:
            px, py = ox + odx, oy + ody
            if not legal(px, py):
                continue
            d1 = cheb(nx, ny, px, py)
            val = opp_obj(d1, opp_evader)
            if best_opp_val is None or val > best_opp_val:
                best_opp_val = val
                best_opp = (odx, ody)
            elif val == best_opp_val and (px, py) < (ox + (best_opp[0] if best_opp else 0), oy + (best_opp[1] if best_opp else 0)):
                best_opp = (odx, ody)

        if best_opp is None:
            continue
        px, py = ox + best_opp[0], oy + best_opp[1]
        d2 = cheb(nx, ny, px, py)
        score = d2 if me_evader else -d2

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]