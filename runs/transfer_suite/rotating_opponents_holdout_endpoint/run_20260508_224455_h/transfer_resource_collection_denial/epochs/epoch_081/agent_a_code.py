def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources") or [])]
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    # Pick target resource: maximize (opponent_distance - self_distance), break ties by smaller self distance.
    # Heavily penalize resources we are behind on.
    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # advantage first; if behind, still consider but with large penalty
        adv = do - ds
        score = (adv * 1000) - (ds * 3) - (0 if adv >= 0 else 2000)
        cand = (score, -adv, ds, rx, ry)  # maximize score; then prefer being less "behind"
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]

    tx, ty = best[3], best[4]
    # If already on target resource, stay (deterministic).
    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Choose next move that minimizes self distance to target, while avoiding obstacles and reducing opponent pressure.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = manh(nx, ny, tx, ty)
        # opponent pressure: how close opponent is to the same target
        do = manh(ox, oy, tx, ty)
        # encourage moving into states that increase our lead (smaller ds2 vs do)
        lead = do - ds2
        # slight tie-break: avoid stepping adjacent to opponent if we don't improve
        adj_opp = max(abs(nx - ox), abs(ny - oy)) <= 1
        penalty = 50 if adj_opp and lead <= (do - manh(sx, sy, tx, ty)) else 0
        # also avoid wasting moves: prefer progress towards target
        prog = manh(sx, sy, tx, ty) - ds2
        cand = (lead * 1000 + prog * 10 - penalty, -ds2, - (dx == 0 and dy == 0), dx, dy)
        if best_move is None or cand > best_move:
            best_move = cand

    if best_move is None:
        return [0, 0]
    return [int(best_move[3]), int(best_move[4])]