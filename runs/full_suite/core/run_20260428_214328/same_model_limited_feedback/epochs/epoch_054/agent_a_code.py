def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    cand_moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d): return max(abs(a-c), abs(b-d))
    def step_toward(tx, ty, x, y):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return dx, dy
    # Pick a resource we can likely reach sooner than opponent: maximize (opp_dist - self_dist)
    best_r = None
    best_s = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        s = do - ds
        # tie-break: prefer closer overall to avoid dithering
        s = s * 100 - (ds + 0.1 * do)
        if s > best_s:
            best_s = s
            best_r = (rx, ry)
    if best_r is None:
        # fallback: move toward center
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_r
    # Evaluate possible moves locally with a "win-denial" heuristic
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in cand_moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            v = -10**12
        else:
            # closer to target is good; also try to keep opponent far from that same target
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # if moving onto/adjacent to a resource, bias strongly
            adj_res = 0
            for rx, ry in resources:
                if max(abs(nx - rx), abs(ny - ry)) == 0:
                    adj_res = 5
                    break
                if max(abs(nx - rx), abs(ny - ry)) == 1:
                    adj_res = max(adj_res, 2)
            # move that improves our lead over opponent more is better
            lead_now = (d_opp - d_self)
            v = (lead_now * 20) - (d_self * 3) + adj_res * 50
            # slight preference to reduce distance to opponent to contest center if tied
            v -= cheb(nx, ny, ox, oy) * 0.5
            # discourage stepping into "direct line" toward target if that step is blocked (simple check)
            sd_x, sd_y = step_toward(tx, ty, sx, sy)
            if (dx, dy) == (sd_x, sd_y):
                # if next step would hit obstacle, penalize
                nx2, ny2 = nx + sd_x, ny + sd_y
                if inb(nx2, ny2) and (nx2, ny2) in obstacles:
                    v -= 30
        if v > best_v:
            best_v = v
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]