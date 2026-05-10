def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    sr = str(observation.get("self_role") or "").lower()
    orr = str(observation.get("opponent_role") or "").lower()
    evader = ("evad" in sr) and ("evad" not in orr)

    resources = observation.get("resources") or []
    res_list = []
    for p in resources:
        try:
            x, y = p
            res_list.append((int(x), int(y)))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def best_resource_score(nx, ny):
        if not res_list:
            return None
        best = 10**18
        for rx, ry in res_list:
            if inb(rx, ry) and (rx, ry) not in obs:
                best = min(best, d2(nx, ny, rx, ry))
        return best if best < 10**18 else None

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        opp_dist = d2(nx, ny, ox, oy)
        val = (-opp_dist) if evader else opp_dist

        rbest = best_resource_score(nx, ny)
        if rbest is not None:
            # prefer getting closer to resources (or just use it as tie-break)
            val += (-rbest if not evader else (rbest // 2))

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_val is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]