def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a target where we are relatively competitive (smaller mydist, larger oppdist).
    best_t = None
    best_score = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Favor resources where we can arrive no later, otherwise still some chance.
        score = (od - sd) + (1.0 / (sd + 1)) - 0.5 * (sd - od > 0)
        if best_score is None or score > best_score:
            best_score, best_t = score, (rx, ry)

    rx, ry = best_t

    # Obstacle-aware move selection: approach target while making opponent farther.
    best = None
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_next = man(nx, ny, rx, ry)
        opp_next = man(nx, ny, ox, oy)  # proxy: moves that keep pressure away from opponent
        oppdist_to_target = man(ox, oy, rx, ry)

        # Stronger: prefer moves that don't reduce our distance advantage.
        # We estimate opponent next distance to target by how much the opponent could close from its current pos.
        # Deterministic heuristic: if our move moves closer to target than opponent can, it's good.
        my_vs_opp = my_next - man(ox, oy, rx, ry)

        # Penalty if near obstacles (discourage risky corridors).
        adj_block = 0
        if (nx + 1, ny) in obstacles or (nx - 1, ny) in obstacles or (nx, ny + 1) in obstacles or (nx, ny - 1) in obstacles:
            adj_block = 1

        mscore = (my_next * 1.2) - (oppdist_to_target * 0.2) + (my_vs_opp * 0.8) - (opp_next * 0.05) + adj_block * 1.5
        if best is None or mscore < best:
            best, best_m = mscore, (dx, dy)

    return [best_m[0], best_m[1]] if best_m is not None else [0, 0]