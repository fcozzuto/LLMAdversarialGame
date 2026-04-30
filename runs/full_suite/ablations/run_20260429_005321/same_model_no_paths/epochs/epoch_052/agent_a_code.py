def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_pen = 2.0

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    best = None
    best_score = -10**9
    if resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            res_dist = min(abs(nx - rx) if abs(nx - rx) > abs(ny - ry) else abs(ny - ry) for rx, ry in resources)
            odx, ody = abs(nx - ox), abs(ny - oy)
            opp_d = odx if odx > ody else ody
            score = -res_dist - (opp_pen / (1 + opp_d))
            if score > best_score:
                best_score = score
                best = [dx, dy]
    if best is None:
        # Fallback: move to reduce distance to opponent while avoiding obstacles
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d0x, d0y = abs(sx - ox), abs(sy - oy)
            cur_d = d0x if d0x > d0y else d0y
            d1x, d1y = abs(nx - ox), abs(ny - oy)
            nxt_d = d1x if d1x > d1y else d1y
            score = (cur_d - nxt_d)  # prefer moving closer
            if best is None or score > best_score:
                best_score = score
                best = [dx, dy]
        if best is None:
            return [0, 0]
    return best