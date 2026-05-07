def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tx_center, ty_center = (w - 1) // 2, (h - 1) // 2

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_val = -10**18

    # If no resources, head toward center
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            val = -cheb(nx, ny, tx_center, ty_center)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Evaluate possible next move by best achievable resource advantage after moving one step.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        # Choose deterministically the most favorable resource for us next turn.
        best_res_val = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can get much sooner; penalize our travel time; slightly reward denying (opponent farther).
            val = (do - ds) * 1000 - ds
            # Tie-break: prefer closer/central resources consistently.
            val += -cheb(rx, ry, tx_center, ty_center) * 2
            if val > best_res_val:
                best_res_val = val
        # Mild preference to keep moving (avoid standing still) if equally good.
        if dx == 0 and dy == 0:
            best_res_val -= 3
        # Also avoid moves that bring us adjacent to too many obstacles? (light deterministic term)
        if (nx, ny) in obstacles:
            best_res_val -= 10**9
        if best_res_val > best_val:
            best_val = best_res_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]