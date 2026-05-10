def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    op_list = [(x, y) for x, y in op_t if 0 <= x < w and 0 <= y < h]
    my_list = [(x, y) for x, y in my_t if 0 <= x < w and 0 <= y < h]
    un_list = [(x, y) for x, y in unclaimed if 0 <= x < w and 0 <= y < h]
    obs_set = {(x, y) for x, y in obstacles if 0 <= x < w and 0 <= y < h}
    my_set = set(my_list)
    op_set = set(op_list)
    un_set = set(un_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not op_list and not un_list:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if ax == cx else (1 if ax < cx else -1)
        dy = 0 if ay == cy else (1 if ay < cy else -1)
        return [dx, dy]

    # Opponent "frontier": cells adjacent (8-neighborhood) to opponent territory that are unclaimed.
    frontier = set()
    for px, py in op_list:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = px + dx, py + dy
                if inb(nx, ny) and (nx, ny) not in op_set:
                    if (nx, ny) in un_set or (nx, ny) not in my_set:
                        frontier.add((nx, ny))

    # Fallback target sets
    targets = list(frontier) if frontier else (un_list if un_list else op_list)

    # Opponent centroid for deterministic tie-break
    ocx = sum(x for x, y in op_list) / len(op_list) if op_list else (w - 1) / 2
    ocy = sum(y for x, y in op_list) / len(op_list) if op_list else (h - 1) / 2

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9
    best_dist = 10**9

    for dx, dy in deltas:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            # If obstacle, staying is enforced; evaluate as staying (0,0) to keep deterministic.
            nx, ny = ax, ay
            dx, dy = 0, 0

        gain = 0
        if (nx, ny) in op_set:
            gain += 50  # flipping counterclaim
        if (nx, ny) in un_set:
            gain += 20
        if (nx, ny) in my_set:
            gain += 5  # maintain territory

        # Progress toward targets
        md = 999
        for tx, ty in targets[:30]:
            d = abs(tx - nx) + abs(ty - ny)
            if d < md:
                md = d

        # Encourage moving closer to opponent centroid once on frontier
        cen = abs(nx - ocx) + abs(ny - ocy)
        score = gain * 10 - md - cen * 0.01

        # Deterministic tie-break: prefer moves with smaller md, then lower (dx,dy) lexicographically
        if score > best_score or (score == best_score and (md < best_dist or (md == best_dist and (dx, dy) < best_move))):
            best_score = score
            best_dist = md
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]