def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    obs_set = {(x, y) for x, y in obstacles if 0 <= x < w and 0 <= y < h}
    my_set = {(x, y) for x, y in my_t if 0 <= x < w and 0 <= y < h}
    op_set = {(x, y) for x, y in op_t if 0 <= x < w and 0 <= y < h}
    un_set = {(x, y) for x, y in unclaimed if 0 <= x < w and 0 <= y < h}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Build deterministic frontier target: unclaimed adjacent to opponent territory, otherwise best unclaimed, else (0,0)
    frontier = []
    for ux, uy in un_set:
        adj_op = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = ux + dx, uy + dy
                    if inb(nx, ny) and (nx, ny) in op_set:
                        adj_op = True
                        break
            if adj_op:
                break
        if adj_op:
            frontier.append((ux, uy))
    candidates = frontier if frontier else (list(un_set) if un_set else [(0, 0)])

    # Deterministically pick: prefer closest to self, tie-break by x,y
    tx, ty = sorted(candidates, key=lambda p: (abs(p[0] - ax) + abs(p[1] - ay), p[0], p[1]))[0]

    # Evaluate moves with explicit territory-based value and distance reduction
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        score = 0
        if (nx, ny) in op_set:
            score += 500  # flipping opponent territory
        elif (nx, ny) in un_set:
            score += 120  # expanding into unclaimed
        elif (nx, ny) in my_set:
            score += 10   # holding
        else:
            score += 20   # should be rare; safe hold
        # Prefer moving toward target (use Chebyshev as diagonal allowed)
        dist_now = max(abs(ax - tx), abs(ay - ty))
        dist_next = max(abs(nx - tx), abs(ny - ty))
        score += (dist_now - dist_next) * 30
        # Small bias to avoid staying still unless necessary
        if dx == 0 and dy == 0:
            score -= 5
        # Deterministic tie-break
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    if best_move == [0, 0]:
        # If all moves blocked, stay
        return [0, 0]
    return best_move