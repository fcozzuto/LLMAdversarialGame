def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    center = (w // 2, h // 2)
    best = (0, 0)
    best_score = -10**18

    # Precompute opponent adjacency cells (favor attacking their border)
    adj_opp = set()
    for (tx, ty) in opp_terr:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = tx + dx, ty + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                adj_opp.add((nx, ny))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        # Base preferences
        if cell in opp_terr:
            type_bonus = 120  # flipping opponent territory on entry
        elif cell in unclaimed:
            type_bonus = 40   # safe expansion; increases controlled area
        elif cell in self_terr:
            type_bonus = 10   # maintain control; avoid wandering
        else:
            type_bonus = 5    # (rare) neutral cell

        # Tactical shaping
        d_to_opp = man(nx, ny, ox, oy)
        d_to_ctr = man(nx, ny, center[0], center[1])

        # If we move onto/near opponent frontier, prioritize heavily
        frontier_bonus = 0
        if cell in adj_opp:
            frontier_bonus += 55
        if cell in unclaimed:
            if cell in adj_opp:
                frontier_bonus += 25
            # Prefer unclaimed that are closer to opponent (threaten quick flip lines)
            frontier_bonus += max(0, 18 - d_to_opp)

        # Avoid getting too far from our own controlled area early if opponent is close
        cohesion_penalty = 0
        if self_terr:
            d_to_self = min(man(nx, ny, px, py) for (px, py) in self_terr)
            cohesion_penalty = max(0, 10 - d_to_self)

        # Deterministic combine
        score = (type_bonus + frontier_bonus) - 0.8 * d_to_opp - 0.25 * d_to_ctr - 2.0 * cohesion_penalty

        # Small tie-break: prefer diagonal (more aggressive territory sweep) then toward opponent
        if score > best_score or (score == best_score and (dx, dy) != best and (dx != 0 and dy != 0)):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]