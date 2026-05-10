def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    def to_pos(p):
        try:
            return int(p[0]), int(p[1])
        except Exception:
            return None

    obstacles = set()
    for p in observation.get("obstacles") or []:
        q = to_pos(p) if p is not None else None
        if q:
            x, y = q
            if 0 <= x < W and 0 <= y < H:
                obstacles.add(q)

    selfT, oppT, unclaimed = set(), set(), set()
    for p in observation.get("self_territory") or []:
        q = to_pos(p) if p is not None else None
        if q:
            selfT.add(q)
    for p in observation.get("opponent_territory") or []:
        q = to_pos(p) if p is not None else None
        if q:
            oppT.add(q)
    for p in observation.get("unclaimed_cells") or []:
        q = to_pos(p) if p is not None else None
        if q:
            unclaimed.add(q)

    resource_cells = set()
    for p in observation.get("resources") or []:
        q = to_pos(p) if p is not None else None
        if q:
            resource_cells.add(q)

    opp_pos = observation.get("opponent_position") or (W - 1, H - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    moves = [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 6
        if (nx, ny) in resource_cells:
            score += 4
        if (nx, ny) in oppT:
            score -= 7
        if (nx, ny) in selfT:
            score += 1

        dist = abs(nx - ox) + abs(ny - oy)
        score += max(0, 4 - dist)  # avoid getting too close when possible

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move