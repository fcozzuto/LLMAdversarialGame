def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    opp_is_evader = ("evad" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role)
    evader = self_is_evader or not opp_is_evader

    resources = observation.get("resources", None) or []
    res_list = [tuple(p) for p in resources] if isinstance(resources, list) else []
    best = None
    best_sc = -10**18 if evader else 10**18

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_opp = dist2(nx, ny, ox, oy)
        if res_list:
            d_res = min(dist2(nx, ny, rx, ry) for rx, ry in res_list)
        else:
            d_res = 0
        sc = (d_opp + 0.15 * d_res) if evader else (-d_opp - 0.15 * d_res)
        if (evader and sc > best_sc) or ((not evader) and sc < best_sc):
            best_sc = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]