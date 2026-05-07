def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    obs_set = set()
    for p in obstacles:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        ax = abs(dx)
        ay = abs(dy)
        return ax if ax > ay else ay

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    if not resources:
        return [0, 0]

    best_score = None
    best_t = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs_set:
            continue
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - md  # >0 means we arrive no later
        # When few resources remain, prioritize certainty for close resources.
        # Otherwise, exploit opportunities where opponent is slower.
        if rem <= 4:
            s = (-md, tx, ty)  # tuple compare: smallest md best
        else:
            s = (-adv, md, tx, ty)  # larger adv best => smaller -adv
        # Primary preference: maximize our advantage; tie-break by deterministic coords
        # Combine into a single comparable tuple.
        if best_score is None or (s, adv) < (best_score, best_score_adv):
            best_score = s
            best_score_adv = adv
            best_t = (tx, ty)
        elif s == best_score and adv > best_score_adv:
            best_score = s
            best_score_adv = adv
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_val = None

    # Counter sweep_rows: also prefer staying in opponent-unfavorable direction.
    # Heuristic value: reduce distance to target, and slightly increase distance from opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Tie-break deterministically: prefer lexicographically smaller move among equals.
        val = (d_to, -d_opp, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]