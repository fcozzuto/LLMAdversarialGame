def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = [0, 0]

    # Deterministic tie-break: iterate resources in stable order
    # (sorted by x then y) to avoid any platform-dependent ordering.
    resources_sorted = sorted(resources, key=lambda p: (p[0], p[1]))

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Choose the best resource achievable after this step.
        chosen_margin = None
        chosen_selfd = None
        chosen_oppd = None

        for rx, ry in resources_sorted:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            margin = oppd - selfd

            # Prefer resources where we arrive strictly sooner; then by how much,
            # then prefer closer self arrival.
            # If we can't beat anyone (margin<=0 for all), fall back to nearest resource.
            if chosen_margin is None:
                chosen_margin, chosen_selfd, chosen_oppd = margin, selfd, oppd
            else:
                # Primary: beat-ability (margin>0), then larger margin
                if (margin > 0) != (chosen_margin > 0):
                    if margin > 0:
                        chosen_margin, chosen_selfd, chosen_oppd = margin, selfd, oppd
                else:
                    if margin > chosen_margin:
                        chosen_margin, chosen_selfd, chosen_oppd = margin, selfd, oppd
                    elif margin == chosen_margin:
                        if selfd < chosen_selfd:
                            chosen_selfd, chosen_oppd = selfd, oppd
                        elif selfd == chosen_selfd and oppd < chosen_oppd:
                            chosen_selfd, chosen_oppd = selfd, oppd

        # Second-stage: ensure robustness against opponent sweeping.
        # If we can beat some resource, maximize beat margin; otherwise minimize our distance.
        if chosen_margin > 0:
            score = (0, -chosen_margin, chosen_selfd, chosen_oppd)
        else:
            # fallback: minimize our distance, but still consider opponent proximity to reduce immediate contest loss
            score = (1, chosen_selfd, chosen_oppd - chosen_selfd)

        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move