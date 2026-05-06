def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Pick an advantageous target deterministically
    if resources:
        best_r = None
        best_key = None
        for r in resources:
            rx, ry = r
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources where we are not behind; then reduce our distance; then favor closeness to opponent (to deny)
            behind = 1 if sd > od else 0
            key = (behind, sd, -od, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = r
    else:
        best_r = None

    # Evaluate candidate moves
    # If no resources or we are too far behind everything, drift to contest the midpoint.
    mx, my = (sx + ox) // 2, (sy + oy) // 2
    best_move = (0, 0)
    best_val = None

    for dx, dy, nx, ny in moves:
        if best_r is None:
            val = -man(nx, ny, mx, my)
        else:
            rx, ry = best_r
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Try to get to the target before opponent; also deny by comparing to opponent distance from our candidate.
            val = (od - sd) * 5 - sd

            # Additional deny/redirect: if any other resource becomes strictly more favorable after this move, boost.
            if resources:
                local_best = -10**9
                for r in resources:
                    rr_x, rr_y = r
                    sdd = man(nx, ny, rr_x, rr_y)
                    odd = man(ox, oy, rr_x, rr_y)
                    behind = 1 if sdd > odd else 0
                    local_key = (behind, sdd, -odd)
                    # Convert key to a numeric improvement proxy
                    imp = (1 - behind) * 1000 - sdd * 3 + odd
                    if imp > local_best:
                        local_best = imp
                val += local_best * 0.05

            # If we are hopelessly behind the chosen target, contest midpoint instead
            if man(sx, sy, rx, ry) > man(ox, oy, rx, ry) + 1:
                val += -man(nx, ny, mx, my) * 0.6

        key = (-(val), dx, dy)  # deterministic tie-break
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]