def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = -10**18

    # Prefer moves that are closer than opponent to at least one resource.
    # Otherwise, "choke" by maximizing the opponent advantage reduction.
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue

            secure = -10**18
            secure_sd = 10**18
            choke = -10**18
            for rx, ry in resources:
                sd = manh(nx, ny, rx, ry)
                od = manh(ox, oy, rx, ry)
                gap = od - sd  # >0 means we are closer
                if gap > 0:
                    # Encourage strong secure gaps, and secondarily closer reach time.
                    val = gap * 100 - sd
                    if val > secure or (val == secure and sd < secure_sd):
                        secure = val
                        secure_sd = sd
                # Always compute best choke metric (max reduction of opponent advantage)
                # Use negative opponent distance to also reduce their roaming.
                val2 = gap * 100 - sd - 0.1 * od
                if val2 > choke:
                    choke = val2

            if secure > -10**17:
                score = secure  # secure a resource
            else:
                # If we can't out-reach, move to minimize how well opponent can reach any resource.
                # This discourages our drift away from the contested region.
                score = choke

            # Tie-break: prefer not moving too far (more stable deterministic paths)
            score -= (abs(dx) + abs(dy)) * 0.01

            if score > best_val:
                best_val = score
                best_move = [dx, dy]

    return best_move