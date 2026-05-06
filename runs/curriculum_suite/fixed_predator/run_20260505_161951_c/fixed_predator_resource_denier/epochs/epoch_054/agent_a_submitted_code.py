def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles", [])
    obs = set(obs_list)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    best_move = (0, 0)
    best_val = -10**18

    def res_pos(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                p = r["position"]
                return int(p[0]), int(p[1])
            for k in ("x", "y"):
                pass
        return None

    res_positions = []
    for r in resources:
        p = res_pos(r)
        if p is not None:
            rx, ry = p
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res_positions.append((rx, ry))

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if res_positions:
            d_self_to_res = min(cheb(nx, ny, rx, ry) for rx, ry in res_positions)
            d_opp_to_res = min(cheb(ox, oy, rx, ry) for rx, ry in res_positions)
            val = (d_opp_to_res - d_self_to_res) * 1000 - cheb(nx, ny, ox, oy)
        else:
            val = cheb(nx, ny, ox, oy) * 2 - cheb(nx, ny, w - 1, h - 1)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]