def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    ox, oy = observation["opponent_position"]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors4(x, y):
        return ((x+1,y),(x-1,y),(x,y+1),(x,y-1))

    # Pick a frontier-ish target to contest sweeping: unclaimed adjacent to our territory,
    # else unclaimed near the opponent (interference).
    frontier = []
    for ux, uy in unclaimed:
        for nx, ny in neighbors4(ux, uy):
            if (nx, ny) in self_terr:
                frontier.append((ux, uy))
                break
    targets = frontier if frontier else list(unclaimed)

    if targets:
        if frontier:
            tx, ty = min(frontier, key=lambda c: abs(c[0]-sx)+abs(c[1]-sy))
        else:
            tx, ty = min(targets, key=lambda c: (abs(c[0]-ox)+abs(c[1]-oy), abs(c[0]-sx)+abs(c[1]-sy)))
    else:
        tx, ty = (ox, oy)  # no unclaimed: try to pressure opponent area

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        # Core: capture unclaimed / flip opponent, while steering toward target.
        score = 0.0
        if cell in unclaimed:
            score += 4.2
        if cell in self_terr:
            score += 0.7
        if cell in opp_terr:
            score += 3.4  # entering flips control

        # Contest: prefer cells near opponent territory to disrupt their sweep.
        near_opp = 0
        for ax, ay in neighbors4(nx, ny):
            if (ax, ay) in opp_terr:
                near_opp += 1
        score += near_opp * 1.1

        # Keep away from obstacles slightly (stability).
        near_obs = 0
        for ax, ay in neighbors4(nx, ny):
            if (ax, ay) in obstacles:
                near_obs += 1
        score -= near_obs * 0.6

        # Move toward target, but don't overcommit.
        score -= 0.35 * (abs(nx - tx) + abs(ny - ty))
        # Also bias toward reducing distance to opponent when contesting.
        score += 0.08 * (abs(nx - ox) + abs(ny - oy) == 0)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]