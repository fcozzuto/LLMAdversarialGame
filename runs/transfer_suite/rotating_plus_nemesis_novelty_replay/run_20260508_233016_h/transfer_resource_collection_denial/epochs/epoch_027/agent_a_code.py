def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a priority target: prefer resources I can reach no later than opponent.
    best = None
    best_rank = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        reachable = 1 if myd <= opd else 0
        # If reachable: fastest; else: try to be as far ahead/deny as possible deterministically.
        rank = (0 if reachable else 1, myd if reachable else myd + 2 * (opd - myd), -opd if reachable else opd)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evaluate each move with a deterministic tie-break; aim closer to target while delaying opponent.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = man(nx, ny, tx, ty)
        opd2 = man(ox, oy, tx, ty)
        # If stepping onto same cell as opponent's "race" path not needed; just delay by maximizing (opponent - me).
        score = (opd2 - myd2) * 10 - myd2
        # Encourage alignment with target early to help against sweep-row nemesis.
        if dx != 0:
            score += -abs((tx - nx)) * 0.01
        if dy != 0:
            score += -abs((ty - ny)) * 0.01
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    # Fallback if all adjacent squares blocked (should be rare)
    return best_move if best_move is not None else [0, 0]