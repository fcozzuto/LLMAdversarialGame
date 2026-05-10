def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not unclaimed:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    # Deterministic anchor: prefer advancing toward the largest unclaimed cluster near our side.
    # Use a small subset for speed and stability.
    un_list = list(unclaimed)
    un_list.sort()
    take = un_list[:32] if len(un_list) > 32 else un_list

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        gain = 0
        if (nx, ny) in unclaimed:
            gain += 5
        elif (nx, ny) in oppT:
            gain += 3
        elif (nx, ny) in selfT:
            gain += 1

        # Immediate positional heuristics
        dopp = dist(nx, ny, ox, oy)
        dopp_now = dist(x, y, ox, oy)
        # If close to opponent, prefer actions that increase separation unless it wins a cell.
        sep_term = (dopp - dopp_now) * 0.25

        # Prefer moving closer to the best local unclaimed cell
        best_local = 10**9
        for tx, ty in take:
            # Favor cells that are closer to us than to opponent (territory edge claim style)
            val = dist(nx, ny, tx, ty) - dist(ox, oy, tx, ty) * 0.15
            if val < best_local:
                best_local = val
        closeness = -best_local * 0.05

        # Avoid dithering: if last move exists, slightly prefer continuing direction
        sp = observation.get("self_path") or []
        last = tuple(sp[-1]) if sp else None
        cont = 0
        if last is not None:
            lx, ly = last
            if (nx, ny) == (lx + (x - lx), ly + (y - ly)):
                cont = 0.3

        score = gain + sep_term + closeness + cont

        # Deterministic tie-break: lexicographic delta
        if score > best_score or (score == best_score and (best is None or (dx, dy) < best)):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]