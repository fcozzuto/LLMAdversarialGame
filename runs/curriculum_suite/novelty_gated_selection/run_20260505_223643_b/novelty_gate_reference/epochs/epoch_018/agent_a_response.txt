def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    res = [(int(p[0]), int(p[1])) for p in resources]
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # If on resource, stay
    for rx, ry in res:
        if rx == sx and ry == sy:
            return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Precompute nearest resource distances
    self_near0 = min(cheb(sx, sy, rx, ry) for rx, ry in res)
    opp_near0 = min(cheb(ox, oy, rx, ry) for rx, ry in res)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        self_d = min(cheb(nx, ny, rx, ry) for rx, ry in res)

        # Heuristic: assume opponent heads for the nearest resource from its position (next-step),
        # so we value pushing away from that nearest target.
        opp_d = cheb(ox, oy, ox + (0 if ox == ox else 0), oy + (0 if oy == oy else 0))  # dummy to keep determinism
        opp_target_dist = min(cheb(ox, oy, rx, ry) for rx, ry in res)
        opp_d = opp_target_dist

        # Avoid obstacle-adjacent traps
        adj_pen = 0
        for ax in (nx - 1, nx, nx + 1):
            for ay in (ny - 1, ny, ny + 1):
                if (ax, ay) in obs:
                    adj_pen += 3

        # Encourage resource-taking and tempo; maximize (opponent advantage reduction + self improvement)
        val = (opp_near0 - opp_d) + (self_near0 - self_d) * 2 - adj_pen

        # Small preference: move toward the single closest resource, deterministic tie-break
        if self_d == 0:
            val += 1000
        else:
            rx_best, ry_best = min(res, key=lambda t: (cheb(nx, ny, t[0], t[1]), t[0], t[1]))
            val -= cheb(ox, oy, rx_best, ry_best) * 0.05

        # Deterministic tie-break: smaller dx^2+dy^2 first, then lexicographic
        dist2 = dx * dx + dy * dy
        if val > best_val or (val == best_val and (dist2 < best_move[0] * best_move[0] + best_move[1] * best_move[1] or
                                                 (dist2 == best_move[0] * best_move[0] + best_move[1] * best_move[1] and (dx, dy) < (best_move[0], best_move[1])))):
            best_val = val
            best_move = [dx, dy]

    return best_move