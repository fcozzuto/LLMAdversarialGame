def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If no resources, go to reduce distance to opponent (deterministic)
    if not resources:
        dx = -sign(ox - x)
        dy = -sign(oy - y)
        return [dx, dy]

    # Target selection: deny resources opponent is closer to; otherwise secure easiest advantage.
    best = None
    best_key = None
    for rx, ry in resources:
        d_me = man(x, y, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        diff = d_opp - d_me  # positive => we are closer
        threatened = 1 if diff < 0 else 0
        # Lexicographic: first deny (threatened=1), then most urgent (smallest d_opp), then maximize advantage, then tie by coordinates
        key = (1 - threatened, min(d_opp, 999), -max(diff, -999), d_me, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose actual move: pick deterministic move that minimizes distance to target and avoids obstacles.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        dm = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)
        # Slightly prefer moves that also increase our lead vs opponent near the target region
        lead_now = man(ox, oy, tx, ty) - dm
        score = (dm, -lead_now, do, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    # If all candidate moves were blocked, stay (engine will keep position)
    return best_move if best_score is not None else [0, 0]