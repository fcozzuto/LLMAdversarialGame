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

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or (("evader" in opp_role) and ("pursuer" not in self_role))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def sign(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    sd_x, sd_y = sign(ox - sx), sign(oy - sy)

    def score_move(nx, ny):
        dx = nx - ox
        dy = ny - oy
        cheb = max(abs(dx), abs(dy))
        manh = abs(dx) + abs(dy)
        # wall-running heuristic: prefer having more "escape" around us if evader, less if pursuer
        neigh_free = 0
        for adx, ady in dirs:
            tx, ty = nx + adx, ny + ady
            if (adx != 0 or ady != 0) and in_bounds(tx, ty):
                neigh_free += 1
        # directional bias to keep pressure aligned (pursuer) / increase separation (evader)
        align = (sd_x == sign(ox - nx) if (ox != nx) else True) and (sd_y == sign(oy - ny) if (oy != ny) else True)
        align_bonus = 0.5 if align else 0.0

        # Add obstacle "turning" bias: if the straightforward direction is blocked, encourage sidestep.
        direct_ok = in_bounds(sx + sd_x, sy + sd_y)
        direct_moves = (nx == sx + sd_x and ny == sy + sd_y)
        block_bias = 0.0
        if not direct_ok and direct_moves:
            block_bias = -2.0 if not is_evader else -1.0
        if direct_ok and (not direct_moves):
            block_bias = -0.2 if not is_evader else -0.1

        if is_evader:
            # maximize cheb first; then manh; then escape freedom
            return (cheb * 10.0) + (manh * 0.2) + (neigh_free * 0.1) + align_bonus + block_bias
        else:
            # minimize cheb first; then manh; then reduce freedom
            return (-cheb * 10.0) + (-manh * 0.2) + (neigh_free * -0.1) + align_bonus + block_bias

    best_move = [0, 0]
    best_val = None
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not in_bounds(nx, ny):
            continue
        v = score_move(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best_move = [ddx, ddy]
    return best_move