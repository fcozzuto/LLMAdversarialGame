def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    viable = []
    for r in resources:
        rx, ry = r[0], r[1]
        if inb(rx, ry) and (rx, ry) not in blocked:
            viable.append((rx, ry))

    # Choose a target that favors a real contest shift (not just nearest).
    # Key uses: prefer resources where we are closer by margin; if none, prefer max (my-opp) distance advantage.
    if viable:
        best = None
        best_key = None
        for rx, ry in viable:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - myd  # positive means we're sooner
            # Deterministic belt tie-break + prefer reachable targets (lower myd)
            belt = abs((rx + ry) - (sx + sy))
            key = (-margin, myd, belt, rx, ry) if margin < 0 else (-(10**6 + margin), myd, belt, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources: head to the corner opposite the opponent.
        tx = 0 if ox > (w - 1) // 2 else w - 1
        ty = 0 if oy > (h - 1) // 2 else h - 1

    # Opponent move approximation: greedy one-step towards the target avoiding obstacles.
    def opp_greedy(nx0, ny0):
        bestd = None
        best_move = (0, 0)
        # Deterministic tie-break: earlier in moves list wins.
        for dx, dy in moves:
            nx, ny = nx0 + dx, ny0 + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            d = cheb(nx, ny, tx, ty)
            if bestd is None or d < bestd:
                bestd = d
                best_move = (dx, dy)
        return best_move

    # Evaluate each of our moves by maximizing "contest leverage" vs opponent's greedy response.
    best_score = None
    best_delta = (0, 0)
    oxm, oym = opp_greedy(ox, oy)
    # If our move changes target dynamics only via our position, still worth using the same target response.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        myd = cheb(nx, ny, tx, ty)
        od_next = cheb(ox + oxm, oy + oym, tx, ty)
        # Prefer moves that improve our distance and worsen the opponent's (relative).
        # Mild preference for staying off obstacles already handled; add tiny bias toward moving.
        score = (od_next - myd, -myd, -(abs(dx) + abs(dy)), nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]