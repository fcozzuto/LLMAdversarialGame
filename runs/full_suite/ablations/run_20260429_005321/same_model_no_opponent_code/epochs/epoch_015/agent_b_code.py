def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obst = {(p[0], p[1]) for p in obstacles}

    deltas = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def cd2(ax, ay, bx, by):
        dx, dy = abs(ax - bx), abs(ay - by)
        return max(dx, dy)  # Chebyshev
    def near_obst(nx, ny):
        k = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            px, py = nx+dx, ny+dy
            if (px, py) in obst: k += 1
        return k

    # If resources exist, choose the move that maximizes "being closer than opponent" after moving.
    best_dx, best_dy = 0, 0
    best_score = -10**18

    if resources:
        # Precompute a compact target set to keep deterministic and fast: best few by advantage.
        targets = []
        for rx, ry in resources:
            ds = cd2(x, y, rx, ry)
            do = cd2(ox, oy, rx, ry)
            # Encourage picking resources where we can get there first.
            # Prefer closer absolute distance as tie-break.
            score = (do - ds) * 100 - ds
            targets.append((score, rx, ry))
        targets.sort(reverse=True)
        targets = targets[:6]

        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue

            # Evaluate using the best target after the move.
            local_best = -10**18
            for _, rx, ry in targets:
                ds2 = cd2(nx, ny, rx, ry)
                do2 = cd2(ox, oy, rx, ry)
                # Small penalty if we are adjacent to obstacles (risk).
                val = (do2 - ds2) * 100 - ds2 - 2 * near_obst(nx, ny)
                # Extra reward if we would land on a resource.
                if (nx, ny) == (rx, ry):
                    val += 500
                if val > local_best:
                    local_best = val

            # Secondary: avoid letting opponent immediately take a nearby resource by not increasing our distance too much.
            # (one-step look: discourage moving away from current best resource)
            best_score_move = local_best
            if best_score_move > best_score:
                best_score = best_score_move
                best_dx, best_dy = dx, dy

    else:
        # No resources visible: move to a safer corner away from opponent to deny.
        tx = 0 if ox > x else w - 1
        ty = 0 if oy > y else h - 1
        curd = cd2(x, y, tx, ty)
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            nd = cd2(nx, ny, tx, ty)
            val = (curd - nd) * 50 - 3 * near_obst(nx, ny)  # prefer progress
            if val > best_score:
                best_score = val
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]