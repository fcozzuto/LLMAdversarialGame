def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def opp_next_towards(rx, ry):
        best = (0, 0)
        bestd = 10**9
        for dx, dy in deltas:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, rx, ry)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return best

    best_move = (0, 0)
    best_val = -10**18

    # Precompute opponent greedy next distances per resource
    opp_next_dist = {}
    for rx, ry in resources:
        odx, ody = opp_next_towards(rx, ry)
        nnx, nny = ox + odx, oy + ody
        opp_next_dist[(rx, ry)] = cheb(nnx, nny, rx, ry)

    cur_resources = resources
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        myd0 = cheb(sx, sy, ox, oy)  # small tie-break proxy
        val = 0
        for rx, ry in cur_resources:
            myd1 = cheb(nx, ny, rx, ry)
            opd1 = opp_next_dist[(rx, ry)]
            cur_my = cheb(sx, sy, rx, ry)
            cur_op = cheb(ox, oy, rx, ry)

            # Avoid resources where opponent is already too close and likely to deny
            if cur_op <= 1:
                continue

            # Prefer resources where I move closer than opponent can after their greedy step
            advantage = (opd1 - myd1)
            progress = (cur_my - myd1)

            # Penalize landing on/near opponent distance to the resource to reduce denial risk
            val += advantage * 40 + progress * 8 - myd1

        # If all resources were skipped, just move away/toward safer direction
        if val == 0 and len(cur_resources) > 0:
            val = -cheb(nx, ny, ox, oy) - cheb(nx, ny, sx, sy)

        # Deterministic tie-break: closer to center of resource set via sum distances
        if val > best_val or (val == best_val and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]