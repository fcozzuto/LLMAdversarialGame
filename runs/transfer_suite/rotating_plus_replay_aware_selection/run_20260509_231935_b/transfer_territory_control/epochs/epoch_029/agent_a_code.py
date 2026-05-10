def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]

    obs_cells = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    un_set = set(unclaimed)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    # Precompute nearest target distances using only existing lists.
    if unclaimed:
        un_list = unclaimed
    else:
        un_list = []
    opp_list = list(opp_set) if opp_set else []

    # Local evaluation with small deterministic tie-break.
    # Goal: claim/secure frontier squares, then pressure opponent territory.
    best = None
    best_score = -1e18
    # Deterministic ordering changes with turn_index to reduce loops.
    k = int(observation.get("turn_index", 0)) % 9
    for i in range(9):
        dx, dy = dirs[(i + k) % 9]
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_cells:
            continue

        cell_self = (nx, ny) in self_set
        cell_opp = (nx, ny) in opp_set
        cell_un = (nx, ny) in un_set

        # Neighborhood frontier density (how many unclaimed around candidate).
        neigh = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in un_set:
                    neigh += 1

        # Distance to nearest unclaimed / opponent cell (Manhattan).
        # If no unclaimed, use opponent cells to keep pressure.
        dist_u = 0
        if un_list:
            dist_u = min(abs(tx - nx) + abs(ty - ny) for (tx, ty) in un_list)
        dist_o = 0
        if opp_list:
            dist_o = min(abs(tx - nx) + abs(ty - ny) for (tx, ty) in opp_list)

        score = 0.0
        # Immediate cell value
        if cell_self:
            score += 1.2
        if cell_un:
            score += 4.2
        if cell_opp:
            score += 8.0  # flipping territory pressure
        # Frontier shaping
        score += 0.35 * neigh
        if un_list:
            score += -0.55 * dist_u
        elif opp_list:
            score += -0.35 * dist_o

        # Prefer staying within bounds and avoid "wasting" move into opponent if unclaimed exists.
        if un_list and cell_opp:
            score -= 2.5

        # Small preference to reduce zig-zag: favor moves that keep direction alignment.
        # Use relative position to own corner for deterministic bias.
        # (top-left corner is (0,0); own corner likely near it or mirrored, but bias still works.)
        bias = (nx + ny) * 0.01
        if cell_self:
            bias += 0.005
        score += bias

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]