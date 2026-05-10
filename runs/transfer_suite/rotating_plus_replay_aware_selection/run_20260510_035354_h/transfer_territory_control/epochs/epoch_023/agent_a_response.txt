def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = {(x, y) for x, y in obstacles if inb(x, y)}
    un_set = {(x, y) for x, y in unclaimed if inb(x, y)}
    my_set = {(x, y) for x, y in my_t if inb(x, y)}
    op_set = {(x, y) for x, y in op_t if inb(x, y)}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**9
    best_move = (0, 0)

    # Aim to break counterclaim patterns: push into unclaimed first; if none, contest opponent territory
    target_list = list(un_set) if un_set else list(op_set)

    # Prefer avoiding immediate obstacle collisions; treat out-of-bounds as invalid (stay)
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        score = 0
        if (nx, ny) in un_set:
            score += 4.0
        if (nx, ny) in op_set:
            score += 1.6  # flipping on entry helps
        if (nx, ny) in my_set:
            score += 0.1

        # Deterministic shaping: move closer to nearest target (unclaimed else opponent territory)
        if target_list:
            mind = 10**9
            for tx, ty in target_list:
                d = abs(tx - nx) + abs(ty - ny)
                if d < mind:
                    mind = d
            # Small reward for closeness to encourage reaching frontier quickly
            score += max(0.0, 2.0 - 0.2 * mind)

        # Avoid moving into cells that are "surrounded" by opponent territory (likely to get counterclaimed)
        neigh = 0
        opp_neigh = 0
        for sx in (-1, 0, 1):
            for sy in (-1, 0, 1):
                if sx == 0 and sy == 0:
                    continue
                xx, yy = nx + sx, ny + sy
                if inb(xx, yy) and (xx, yy) not in obs_set:
                    neigh += 1
                    if (xx, yy) in op_set:
                        opp_neigh += 1
        if neigh > 0:
            score -= 0.25 * (opp_neigh / neigh)

        # Tie-break deterministically toward diagonals that increase x then y (consistent ordering)
        if score > best_score or (score == best_score and (dx, dy) > best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]