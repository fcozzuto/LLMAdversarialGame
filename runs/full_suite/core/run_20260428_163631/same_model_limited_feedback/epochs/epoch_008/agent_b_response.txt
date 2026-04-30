def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # If no resources, hold
    if not resources:
        return [0, 0]

    best_r = None
    best_adv = None
    best_self_d = None
    for i, (rx, ry) in enumerate(resources):
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if best_r is None or adv > best_adv or (adv == best_adv and (sd < best_self_d or (sd == best_self_d and i < best_i))):
            best_r = (rx, ry)
            best_adv = adv
            best_self_d = sd
            best_i = i

    rx, ry = best_r

    best_move = (0, 0)
    best_val = None
    best_next_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        sd_next = cheb(nx, ny, rx, ry)
        od_to_res = cheb(ox, oy, rx, ry)
        # Prefer reaching target quickly; also prefer denying opponent (larger opponent distance relative to ours)
        val = -(sd_next) + 0.15 * (od_to_res - sd_next)
        # Deterministic tie-breakers
        if best_val is None or val > best_val or (val == best_val and (best_next_d is None or sd_next < best_next_d)) or (val == best_val and sd_next == best_next_d and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
            best_next_d = sd_next

    return [int(best_move[0]), int(best_move[1])]