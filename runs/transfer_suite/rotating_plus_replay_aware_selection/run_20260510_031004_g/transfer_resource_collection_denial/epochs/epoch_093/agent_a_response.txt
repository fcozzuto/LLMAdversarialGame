def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    low_turn = int(observation.get("turns_remaining", 0) or 0)
    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    favor_race = 1 if (low_turn > 0 and rem > 2) else 0

    best = None  # key, target
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        lead = opp_d - my_d
        if favor_race:
            # Prefer winning race; then prefer being closer and at larger lead.
            key = (lead, -my_d, -opp_d, rx, ry)
        else:
            # Late game: prioritize nearest to self; but still avoid obvious losing races.
            key = (-my_d, lead, -opp_d, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            my_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            # Score: decrease distance; prefer to keep/extend being ahead in race.
            lead = opp_d - my_d
            score = (lead if favor_race else 0, -my_d, -abs(nx - ox), -abs(ny - oy), -dx * dx - dy * dy)
            moves.append((score, [dx, dy]))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: t[0], reverse=True)
    return moves[0][1]