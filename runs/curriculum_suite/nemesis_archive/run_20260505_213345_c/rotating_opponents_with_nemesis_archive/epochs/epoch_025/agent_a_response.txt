def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    # Manhattan distance on 8x8 grid (diagonals allowed for moves; distance heuristic still works deterministically)
    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection for resource denial: prefer resources where we can arrive sooner than opponent.
    best_target = None
    best_t = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Advantage: positive means we are closer; tie-break by smaller overall distance to reach quickly.
        adv = ds - do
        # Penalize being behind; prefer best advantage, then closest.
        key = (0 if adv < 0 else 1, abs(adv), ds)
        if best_t is None or key < best_t:
            best_t = key
            best_target = (rx, ry)

    rx, ry = best_target
    # If no resource we are closer to, choose the resource minimizing (our distance - opponent distance) after one move.
    # Also incorporate "intercept": move to reduce distance to opponent while still improving our reach to the chosen resource.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        ds1 = md(nx, ny, rx, ry)
        do1 = md(ox, oy, rx, ry)
        ds_to_opp = md(nx, ny, ox, oy)
        # Main objective: become closer than opponent to the target; if already closer, speed up.
        # Secondary: if we can't get closer, move toward opponent to hinder their denial path.
        advantage = ds1 - do1
        score = (1 if advantage >= 0 else 0, abs(advantage), ds1, ds_to_opp)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]