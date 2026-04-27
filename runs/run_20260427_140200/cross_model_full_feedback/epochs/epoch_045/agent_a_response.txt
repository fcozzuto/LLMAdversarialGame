def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for king moves

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a best resource to contest: maximize advantage in arrival time; penalize being too slow.
    best_r = None
    best_pr = -10**18
    for r in resources:
        dm = dist((sx, sy), r)
        do = dist((ox, oy), r)
        pr = (do - dm) * 20 - dm  # contest first, then be close
        # If we are likely to reach it earlier, boost; if opponent earlier, dampen.
        if dm <= do:
            pr += 15
        best = pr
        if best > best_pr:
            best_pr = best
            best_r = r

    # If no resources, just move to increase distance from opponent while heading to center.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if best_r is not None:
            d_m = dist((nx, ny), best_r)
            d_o = dist((ox, oy), best_r)
            # Also consider: reduce opponent's access to that resource by moving away from their approach.
            opp_to_me = dist((ox, oy), (nx, ny))
            val = (d_o - d_m) * 22 - d_m * 2 - opp_to_me * 0.5
            # Encourage taking immediate nearby resources even if not globally best.
            for r2 in resources:
                if dist((nx, ny), r2) == 0:
                    val += 120
                elif dist((nx, ny), r2) == 1:
                    val += 20
        else:
            # Defense/positioning
            val = dist((nx, ny), (ox, oy)) * 8 - (abs(nx - cx) + abs(ny - cy)) * 0.5
        # Deterministic tie-break: prefer smaller (dx,dy) lexicographically after score.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]