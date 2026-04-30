def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs_set = set((p[0], p[1]) for p in obstacles)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res_set = set((r[0], r[1]) for r in resources)

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_move_to_resource(nx, ny, rx, ry):
        md = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Opponent gets at most one step advantage next turn.
        od_eff = od - 1
        if od_eff < 0: od_eff = 0
        md_eff = md
        # Favor contested resources where we are not worse.
        if md_eff <= od_eff:
            return 60 - 3 * md_eff
        # If opponent is threatening (close), try to contest anyway.
        if od_eff <= 2:
            return 15 - 5 * md_eff + 10 * (2 - od_eff)
        return -10 * (md_eff - od_eff)

    best = (0, 0)
    best_score = -10**18

    # Compute a deterministic "resource center" for fallback.
    if resources:
        cx = sum(r[0] for r in resources) // len(resources)
        cy = sum(r[1] for r in resources) // len(resources)
    else:
        cx, cy = W // 2, H // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy
            dx, dy = 0, 0

        if (nx, ny) in res_set:
            return [dx, dy]

        score = 0

        # Primary: maximize advantage over resources with a one-step opponent model.
        for rx, ry in resources:
            score += best_move_to_resource(nx, ny, rx, ry)

        # Secondary: reduce risk by not moving to cells where opponent is extremely close to any resource.
        threatened = 0
        for rx, ry in resources:
            if cheb(ox, oy, rx, ry) <= 1:
                threatened += 1
        score -= threatened * cheb(nx, ny, ox, oy)

        # Tertiary: fallback pressure toward center of resources when ties.
        if not resources:
            score -= cheb(nx, ny, cx, cy)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]