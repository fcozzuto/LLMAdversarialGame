def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(ax, ay, bx, by):
        return abs(ax-bx) + abs(ay-by)

    # Pick a resource that we are closer to; if tie, prefer one that hurts opponent most (bigger opp-self gap).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Primary: minimize self distance (reach sooner), Secondary: maximize opponent disadvantage.
        key = (sd, -(od - sd), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Step toward target with deterministic tie-break and slight anti-overlap: avoid cells where opponent is closer to target than we are after move.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)  # opponent doesn't move yet; we only avoid giving it an easy win
        overlap_penalty = 0
        if resources:
            # If we move to a cell that is also close to the opponent's nearest resource, discourage.
            # (Cheap deterministic signal without full search.)
            mind = 10**9
            for rx, ry in resources:
                mind = min(mind, man(nx, ny, rx, ry) - man(ox, oy, rx, ry))
            overlap_penalty = -mind  # lower mind means relatively worse; convert to penalty
        # Prefer minimal distance to target; if equal, prefer maximizing opponent disadvantage.
        candidates.append((sd2, -((od2 - sd2)), overlap_penalty, nx, ny, dx, dy))

    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    return [candidates[0][5], candidates[0][6]]