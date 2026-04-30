def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inside(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def d(a, b, c, d2):  # Chebyshev
        return max(abs(a-c), abs(b-d2))
    def pick_target():
        if not resources:
            return (w//2, h//2)
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            our = d(x, y, rx, ry)
            opp = d(ox, oy, rx, ry)
            # Prefer resources where we are (or become) closer than opponent; tie-break by our distance then coords.
            key = (-(opp - our), our, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best if best is not None else (w//2, h//2)

    tx, ty = pick_target()
    opp_to_target = d(ox, oy, tx, ty)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            val = -10**17  # invalid -> keep in place
        else:
            our_to_target = d(nx, ny, tx, ty)
            # Core: get to target quickly. Secondary: avoid letting opponent overtake on the same target.
            takeover_gap = our_to_target - opp_to_target  # negative means we are closer than opponent
            val = (-our_to_target * 10) + (takeover_gap * 6)  # being closer (more negative) increases value
            # If landing on a resource tile, strongly prefer it.
            if (nx, ny) in set(tuple(p) for p in resources):
                val += 10**6
            # Small bias toward staying away from opponent to reduce conflicts when neither is clearly closer.
            val -= d(nx, ny, ox, oy) * 0.5
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]