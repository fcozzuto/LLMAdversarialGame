def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def parse_points(key):
        pts = []
        for p in observation.get(key, []) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
            elif isinstance(p, dict):
                if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                    x, y = int(p["position"][0]), int(p["position"][1])
                elif "x" in p and "y" in p:
                    x, y = int(p["x"]), int(p["y"])
                else:
                    continue
            else:
                continue
            if 0 <= x < w and 0 <= y < h:
                pts.append((x, y))
        return pts

    obstacles = set(parse_points("obstacles"))
    resources = parse_points("resources")
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_best = []
    for r in resources:
        opp_best.append((cheb((ox, oy), r), r))
    # prioritize resources closer to opponent less (steal/delay); far from opponent more (safer pick)
    resources_sorted = sorted(resources, key=lambda r: (cheb((ox, oy), r), -cheb((sx, sy), r)))

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        self_d_to_best = 10**9
        opp_d_to_target = 0
        target = resources_sorted[0]
        # select a target that balances closeness for us and distance from opponent
        # (keep deterministic: check fixed order)
        for r in resources_sorted:
            sd = cheb((nx, ny), r)
            od = cheb((ox, oy), r)
            val = (od - sd, -od, -sd)
            if val > (cheb((sx, sy), target)*0, 0, 0):  # neutral comparator to avoid extra state
                target = r
                self_d_to_best, opp_d_to_target = sd, od
        # final evaluation: go where we are relatively closer than opponent, and also prefer stealing over just moving
        rel = opp_d_to_target - self_d_to_best
        # minor keep-away from opponent to discourage direct probe convergence
        opp_close_penalty = -cheb((nx, ny), (ox, oy))
        # slight preference for moving toward any resource if relative is tied
        resource_prox_bonus = -min(cheb((nx, ny), r) for r in resources)
        val = rel * 100 + opp_close_penalty * 2 + resource_prox_bonus
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]