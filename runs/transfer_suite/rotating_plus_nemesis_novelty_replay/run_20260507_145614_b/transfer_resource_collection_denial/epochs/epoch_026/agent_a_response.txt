def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    ox, oy = observation["opponent_position"]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    best_move = [0, 0]
    best_val = -10**18

    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        self_best = -10**18
        for rx, ry in resources:
            if not valid(rx, ry):
                continue
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            steal = od - sd  # positive means we are closer (or will be)
            # Prefer nearer resources too, and prefer moves that keep steal advantage.
            val = steal * 3 - sd
            # If we are far from any resource, slightly bias toward reducing our closest distance.
            self_best = max(self_best, val)

        # Global tie-break: reduce our distance to the single closest resource after move.
        closest_sd = min(abs(rx - nx) + abs(ry - ny) for rx, ry in resources if valid(rx, ry))
        # Secondary: avoid moving adjacent to obstacles only indirectly; use a small stability term.
        stability = -abs(dxm) - abs(dym)

        total = self_best * 10 - closest_sd + stability
        if total > best_val:
            best_val = total
            best_move = [dxm, dym]

    return best_move