def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role_s = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role_s for k in ("evad", "run", "away", "escape", "runner"))
    is_pursuer = ("purs" in role_s) or ("hunt" in role_s) or ("chase" in role_s)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def border_risk(x, y):
        # higher means safer (farther from borders)
        return min(x, y, w - 1 - x, h - 1 - y)

    def nearest_obstacle_dist(x, y):
        md = 10**9
        for bx, by in blocked:
            d = abs(bx - x) + abs(by - y)
            if d < md:
                md = d
        return md if blocked else 4

    # If evader, bias toward increasing distance and toward the center.
    # If pursuer, bias toward decreasing distance and toward moves that approach the evader while avoiding obstacles.
    best_dxdy = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        obs_d = nearest_obstacle_dist(nx, ny)
        center = border_risk(nx, ny)

        # Simple local "trap" check: do we create a move that would allow the pursuer to instantly surround?
        # Approx: count how many free moves from (nx,ny).
        free_next = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty):
                free_next += 1

        if is_evader:
            # Maximize distance, avoid edges a bit, avoid low-mobility squares.
            score = (dist * 2.0) + (center * 0.7) + (obs_d * 0.05) + (free_next * 0.2)
        else:
            # Minimize distance, prefer squares with more escape routes (avoid tight corners), and avoid obstacles slightly.
            score = (-dist * 2.0) + (center * 0.1) + (obs_d * 0.02) + (free_next * 0.15)

        # Deterministic tie-break: prefer lexicographically smaller move deltas.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_dxdy):
            best_score = score
            best_dxdy = (dx, dy)

    dx, dy = best_dxdy
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]