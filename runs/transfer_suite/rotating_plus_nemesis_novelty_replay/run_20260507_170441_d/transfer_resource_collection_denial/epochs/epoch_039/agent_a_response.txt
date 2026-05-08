def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None:
            obst.add((p[0], p[1]))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def dist(x1, y1, x2, y2):
        return max(abs(x1-x2), abs(y1-y2))  # Chebyshev for diagonal moves

    if not resources:
        return [0, 0]

    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate move by how well we can beat opponent on some resource, else by closeness.
        top = -10**9
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # If we are closer, reward strongly; if not, penalize.
            # Also slightly prefer resources already near opponent (denial/contest).
            beat = (opd - myd)
            # If beat positive: likely win; if negative: likely lose.
            score = 6.0 * beat + (-1.0 * myd) + (0.15 * (opd))
            top = score if score > top else top

        # Add small tie-break: move away from obstacles is implicit; also avoid staying still too much.
        stay_pen = 0.08 if (dx == 0 and dy == 0) else 0.0
        # Mildly encourage moving toward the nearest resource overall to prevent degenerate "stall to deny".
        mind = min(dist(nx, ny, rx, ry) for (rx, ry) in resources)
        score2 = top + (-0.2 * mind) - stay_pen

        if best_score is None or score2 > best_score:
            best_score = score2
            best = (dx, dy)

    return [int(best[0]), int(best[1])]