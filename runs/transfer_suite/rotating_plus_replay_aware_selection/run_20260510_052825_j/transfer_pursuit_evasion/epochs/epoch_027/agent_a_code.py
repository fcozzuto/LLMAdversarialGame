def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    if ("evad" in self_role) or (self_role == "evader"):
        mode = "evade"
    elif ("purs" in self_role) or (self_role == "pursuer"):
        mode = "pursue"
    else:
        mode = "pursue" if (("evad" in opponent_role) or (opponent_role == "evader")) else "evade"

    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    # Deterministic tie-break: prefer orthogonal over diagonal, and then smaller dx, then smaller dy
    def tie_key(dx, dy):
        return (1 if abs(dx) == 1 and abs(dy) == 1 else 0, abs(dx), abs(dy), dx, dy)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        ddx = nx - ox
        ddy = ny - oy
        dist2 = ddx * ddx + ddy * ddy  # diagonal-friendly

        # Additional obstacle pressure: lightly penalize moving adjacent to obstacles (evader)
        # and reward keeping distance (pursuer). Deterministic and cheap.
        adj = 0
        for ax, ay in ((1,0), (-1,0), (0,1), (0,-1)):
            px, py = nx + ax, ny + ay
            if inb(px, py) and (px, py) in obs:
                adj += 1

        # Score: pursue -> minimize distance; evade -> maximize distance.
        if mode == "pursue":
            score = -dist2 - 0.15 * adj
        else:
            score = dist2 - 0.25 * adj

        if best_score is None or score > best_score or (score == best_score and tie_key(dx, dy) < tie_key(best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]